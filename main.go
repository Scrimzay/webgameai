package main

import (
	"log"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type GameState struct {
	Board [3][3]int `json:"board"`
	CurrentPlayer int `json:"current_player"`
	Winner int `json:"winner"`
}

var game = GameState{Board: [3][3]int{}, CurrentPlayer: 1, Winner: 0}

func newGame(c *gin.Context) {
	game = GameState{Board: [3][3]int{}, CurrentPlayer: 1, Winner: 0}
	c.JSON(http.StatusOK, game)
}

func makeMove(c *gin.Context) {
	rowStr := c.Param("row")
	colStr := c.Param("col")
	row, _ := strconv.Atoi(rowStr)
	col, _ := strconv.Atoi(colStr)

	if game.Board[row][col] != 0 || game.Winner != 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid move"})
		return
	}

	game.Board[row][col] = game.CurrentPlayer
	game.CurrentPlayer = -game.CurrentPlayer

	// Check winner
	game.Winner = checkWinner(game.Board)

	c.JSON(http.StatusOK, game)
}

func getState(c *gin.Context) {
	c.JSON(http.StatusOK, game)
}

func checkWinner(board [3][3]int) int {
	// Rows, cols, diags check; return 1/-1/0. Implement fully
	for i := 0; i < 3; i++ {
		if board[i][0] == board[i][1] && board[i][1] == board[i][2] && board[i][0] != 0 {
			return board[i][0]
		}
		if board[0][i] == board[1][i] && board[1][i] == board[2][i] && board[0][i] != 0 {
			return board[0][i]
		}
	}

	// Diags...
	if board[0][0] == board[1][1] && board[1][1] == board[2][2] && board[0][0] != 0 {
		return board[0][0]
	}
	if board[0][2] == board[1][1] && board[1][1] == board[2][0] && board[0][2] != 0 {
		return board[0][2]
	}

	// Check draw
	full := true
	for i := 0; i < 3; i++ {
		for j := 0; j < 3; j++ {
			if board[i][j] == 0 {
				full = false
			}
		}
	}
	if full {
		return 0
	}
	return 0
}
	
func main() {
	r := gin.Default()
	r.LoadHTMLGlob("**/*.html")
	r.Static("/static", "./static")

	r.GET("/", indexHandler)
	r.GET("/new-game", newGame)
	r.POST("/move/:row/:col", makeMove)
	r.GET("/state", getState)

	err := r.Run(":8080")
	if err != nil {
		log.Fatal(err)
	}
}
	
func indexHandler(c *gin.Context) {
	c.File("public/index.html")
}
