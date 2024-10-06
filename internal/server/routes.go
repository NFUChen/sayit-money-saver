package server

import (
	"commit-gpt/internal/server/commons"
	"net/http"

	"fmt"
	"log"
	"time"

	"github.com/gin-gonic/gin"

	"github.com/coder/websocket"
)

type Router interface {
	GetHandlers() []commons.HttpHandler
}

func (server *Server) RegisterRoutes(engine *gin.Engine, routers []Router) http.Handler {

	engine.GET("/websocket", server.websocketHandler)

	for _, router := range routers {
		handlers := router.GetHandlers()
		for _, handler := range handlers {
			engine.Handle(handler.HttpMethod, handler.Path, handler.Handler)
		}
	}

	return engine
}

func (server *Server) websocketHandler(c *gin.Context) {
	w := c.Writer
	r := c.Request
	socket, err := websocket.Accept(w, r, nil)

	if err != nil {
		log.Printf("could not open websocket: %v", err)
		_, _ = w.Write([]byte("could not open websocket"))
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	defer socket.Close(websocket.StatusGoingAway, "server closing websocket")

	ctx := r.Context()
	socketCtx := socket.CloseRead(ctx)

	for {
		payload := fmt.Sprintf("server timestamp: %d", time.Now().UnixNano())
		err := socket.Write(socketCtx, websocket.MessageText, []byte(payload))
		if err != nil {
			break
		}
		time.Sleep(time.Second * 2)
	}
}
