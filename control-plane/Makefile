.PHONY: build test clean docker run migrate keys

# Build the application
build:
	go build -o control-plane ./cmd/

# Run tests
test:
	go test -v ./...

# Run tests with coverage
test-coverage:
	go test -cover -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html

# Clean build artifacts
clean:
	rm -f control-plane coverage.out coverage.html

# Build Docker image
docker:
	docker build -t areax-control-plane .

# Generate JWT keys
keys:
	./scripts/generate-keys.sh

# Run the application (requires env setup)
run: build
	./control-plane

# Run database migrations (built into startup)
migrate: build
	./control-plane

# Download dependencies
deps:
	go mod download
	go mod tidy

# Format code
fmt:
	go fmt ./...

# Run linter
lint:
	golangci-lint run

# Development setup
dev-setup: keys
	cp .env.example .env
	@echo "Edit .env with your configuration"

# Default target
all: build
