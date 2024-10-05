package service

import (
	"fmt"
	"github.com/gookit/slog"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type SqlConnectionConfig struct {
	UserName     string
	Password     string
	DatabaseName string
	Host         string
	Port         int
}

func (config *SqlConnectionConfig) ToString() string {
	return fmt.Sprintf("host=%v user=%v password=%v dbname=%v port=%d sslmode=disable TimeZone=Asia/Shanghai",
		config.Host, config.UserName, config.Password, config.DatabaseName, config.Port,
	)
}

type ModelMigrationService struct {
	SqlConnectionConfig SqlConnectionConfig
	Engine              *gorm.DB
}

func NewModelMigrationService(config SqlConnectionConfig) *ModelMigrationService {

	engine, err := gorm.Open(postgres.Open(config.ToString()), &gorm.Config{})
	if err != nil {
		slog.Fatal(err)
	}
	return &ModelMigrationService{SqlConnectionConfig: config, Engine: engine}
}

func (service *ModelMigrationService) Migrate(models []any) {

	for _, model := range models {
		err := service.Engine.AutoMigrate(model)
		if err != nil {
			slog.Fatalf("Auto migrate models err: %v", err)
		}
	}

}
