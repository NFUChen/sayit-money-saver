package service

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"github.com/sashabaranov/go-openai"
	"html/template"
	"log/slog"
)

type GptService struct {
	Model     *openai.Client
	ModelType string
}

func NewGptService(apiToken string, modelType string) *GptService {
	client := openai.NewClient(apiToken)
	service := &GptService{
		Model:     client,
		ModelType: modelType,
	}
	return service
}

func (service *GptService) modelPrompt(model any, prompt string, modelMetaPrompt string, currentError string) (string, error) {
	schema, err := json.Marshal(model)
	if err != nil {
		slog.Error(err.Error())
		return "", err
	}

	promptSchema := BasePromptSchema{
		Prompt:     prompt,
		Schema:     string(schema),
		MetaPrompt: modelMetaPrompt,
		Error:      currentError,
	}
	_template, err := template.New("basePrompt").Parse(BasePrompt)
	if err != nil {
		return "", err
	}
	var output bytes.Buffer
	err = _template.Execute(&output, promptSchema)
	if err != nil {
		return "", err
	}
	return output.String(), nil
}

type Model interface {
	Validate() error
	GetMetaPrompt() string
}

func (service *GptService) doAskModel(ctx context.Context, model Model, metaPrompt string, userPrompt string, error string) error {
	prompt, err := service.modelPrompt(model, userPrompt, metaPrompt, error)
	if err != nil {
		return err
	}
	slog.Info(fmt.Sprintf("Model Prompt: %s", prompt))
	resp, err := service.Model.CreateChatCompletion(
		ctx,
		openai.ChatCompletionRequest{
			Model: service.ModelType,
			ResponseFormat: &openai.ChatCompletionResponseFormat{
				Type: "json_object",
			},
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleUser,
					Content: prompt,
				},
			},
		},
	)
	if err != nil {
		return err
	}

	answer := resp.Choices[0].Message.Content
	err = json.Unmarshal([]byte(answer), &model)
	if err != nil {
		slog.Warn(fmt.Sprintf("Assistant response: %v ", answer))
		return fmt.Errorf("failed to unmarshal model response: %v", err)
	}

	err = model.Validate()
	if err != nil {
		return fmt.Errorf("model validation failed: %v", err)
	}
	return nil
}

func (service *GptService) ModelAsk(ctx context.Context, model any, prompt string) error {

	select {
	case <-ctx.Done():
		return ctx.Err()
	default:
		const MaxAttempt = 5
		_model, ok := model.(Model)
		if !ok {
			return fmt.Errorf("model response was not a model interface")
		}
		currentAttempt := 0
		currentError := ""
		for {
			if currentAttempt >= MaxAttempt {
				return fmt.Errorf("max attempt reached after %d attempts", MaxAttempt)
			}
			slog.Info(fmt.Sprintf("[%d] Attempt to ask with prompt: %v", currentAttempt, prompt))

			err := service.doAskModel(ctx, _model, prompt, _model.GetMetaPrompt(), currentError)
			if err == nil {
				break
			}
			currentAttempt += 1
			currentError = err.Error()
			slog.Error(currentError)
		}
		return nil
	}

}
