package main

import (
	"fmt"
	"sync"
	"time"
)

	type Token struct {
		data      string
		recipient int
		ttl       int
	}

	type Node struct {
		id   int // идентификатор узла
		prev <-chan Token
		next chan<- Token
	}

	func (n *Node) message(wg *sync.WaitGroup, N int) {
		defer wg.Done()
		for {
			select {
			case token := <-n.prev: // Получение токена из канала
				if token.ttl == 0 { // Если время жизни токена истекло
					fmt.Printf("Узел %d: время жизни истекло\n", n.id)
					continue
				}
				if token.recipient == n.id { // Если узел это получатель
					fmt.Printf("Узел %d: получено сообщение: %s от узла %d\n", n.id, token.data, (n.id-1+N)%N)
					continue
				}
				//fmt.Printf("Узел %d: Передача сообщения: %s узлу %d\n", n.id, token.data, (n.id+1)%N)
				token.ttl--
				n.next <- token // Отправка токена следующему узлу
			case <-time.After(time.Second * 1):
				return
			}
		}
	}

	func createTokenRing(N int, recipient int, ttl int) {
		var wg sync.WaitGroup
		channels := make([]chan Token, N)
		for i := range channels {
			channels[i] = make(chan Token)
		}
		nodes := make([]Node, N)
		for i := 0; i < N; i++ {
			nodes[i] = Node{i, channels[i], channels[(i+1)%N]}
			wg.Add(1)
			go nodes[i].message(&wg, N)
		}
		channels[0] <- Token{fmt.Sprintf("Сообщения для узла %d!", recipient), recipient, ttl} // Отправка токена первому узлу
		wg.Wait()
		for _, ch := range channels {
			close(ch) // Закрытие всех каналов
		}
	}
	
	func main() {
		var N, recipient, ttl int
		fmt.Print("Введите число узлов: ")
		fmt.Scan(&N)
		fmt.Print("Введите номер адресата: ")
		fmt.Scan(&recipient)
		fmt.Print("Введите срок жизни ttl: ")
		fmt.Scan(&ttl)
		createTokenRing(N, recipient, ttl)
	}
