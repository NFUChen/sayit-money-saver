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

func (service *GptService) askWrapper(ctx context.Context, model Model, prompt string, error string) (Model, error) {
	modelPrompt, err := service.modelPrompt(model, prompt, model.GetMetaPrompt(), error)
	if err != nil {
		return nil, err
	}
	resp, err := service.Model.CreateChatCompletion(
		ctx,
		openai.ChatCompletionRequest{
			Model: service.ModelType,
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleUser,
					Content: modelPrompt,
				},
			},
		},
	)
	if err != nil {
		return nil, err
	}

	// Extract the model's response and unmarshal it into the model object
	answer := resp.Choices[0].Message.Content
	err = json.Unmarshal([]byte(answer), &model)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal model response: %v", err)
	}

	err = model.Validate()
	if err != nil {
		return nil, fmt.Errorf("model validation failed: %v", err)
	}
	return model, nil
}

func (service *GptService) ModelAsk(ctx context.Context, model Model, prompt string) (Model, error) {
	const MaxAttempt = 5
	currentAttempt := 0
	currentError := ""
	for {
		if currentAttempt >= MaxAttempt {
			return nil, fmt.Errorf("max attempt reached after %d attempts", MaxAttempt)
		}
		slog.Info(fmt.Sprintf("[%d] Attempt to ask with prompt: %v", currentAttempt, prompt))
		_, err := service.askWrapper(ctx, model, prompt, currentError)
		if err == nil {
			break
		}
		currentAttempt += 1
		currentError = err.Error()
	}
	return model, nil
}
