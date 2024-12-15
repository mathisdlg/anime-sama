# Docker

Docker is an operating system level virtualization solution for delivering software in packages called containers.

We assume users have Docker correctly installed on their computer if they wish to use this feature. Docker is available for Linux as well as MacOS and Windows. For more details visit: https://www.docker.com/

# Running Anime Sama with Docker

## Quick Start

To run anime-sama with Docker, take the following steps:

```sh
# Clone the repository and change to where the Docker files reside:
git clone --depth=1 git@github.com:mathisdlg/anime-sama.git
cd anime-sama/docker

# Build the Docker image:
docker build -t anime_sama_image -f dockerfile .

# Run the web application:
docker compose up web

# Run the TUI application:
docker compose run tui

# Run all services
docker-compose up

```
