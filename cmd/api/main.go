package main

import (
	"commit-gpt/internal/api"
	"commit-gpt/internal/service"
	"context"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"commit-gpt/internal/server"
)

func gracefulShutdown(apiServer *http.Server) {
	// Create context that listens for the interrupt signal from the OS.
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	// Listen for the interrupt signal.
	<-ctx.Done()

	log.Println("shutting down gracefully, press Ctrl+C again to force")

	// The context is used to inform the server it has 5 seconds to finish
	// the request it is currently handling
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	if err := apiServer.Shutdown(ctx); err != nil {
		log.Printf("Server forced to shutdown with error: %v", err)
	}

	log.Println("Server exiting")
}
func init() {
	err := godotenv.Load()
	if err != nil {
		log.Fatalf("Error loading .env file")
	}
}

func main() {
	engine := gin.Default()
	port, _ := strconv.Atoi(os.Getenv("PORT"))
	sqlPort, _ := strconv.Atoi(os.Getenv("SQL_PORT"))

	sqlConfig := service.SqlConnectionConfig{
		UserName:     os.Getenv("SQL_USER"),
		Password:     os.Getenv("SQL_PASSWORD"),
		DatabaseName: os.Getenv("SQL_DATABASE_NAME"),
		Host:         os.Getenv("SQL_HOST"),
		Port:         sqlPort,
	}

	migrationService := service.NewModelMigrationService(sqlConfig)
	migrationService.Migrate(service.GetAllModels())

	gptService := service.NewGptService(
		os.Getenv("OPENAI_API_KEY"),
		os.Getenv("OPENAI_MODEL"),
	)
	userService := service.NewUserService(migrationService.GetEngine())
	transactionService := service.NewTransactionService(migrationService.GetEngine(), userService)
	moneySaverService := service.NewMoneySaverService(transactionService, gptService, userService)
	routers := []server.Router{
		&api.LineRouter{Engine: engine, MoneySaverService: moneySaverService},
	}
	_server := server.NewServer(port, engine, routers)
	go gracefulShutdown(_server)
	err := _server.ListenAndServe()
	if err != nil {
		return
	}

}
