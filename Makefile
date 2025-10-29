SRC = ./src/main.py

NAME = legacy

$(NAME):
	@make -C geneweb_python

all: $(NAME)

clean:
	@make clean -C geneweb_python

fclean: clean
	@make fclean -C geneweb_python

help:
	@echo "Top-level commands:"
	@printf "  %-20s %s\n" "test-bf" "Run backend and frontend tests with coverage summary"
	@echo ""
	@make help -C geneweb_python

dev-setup:
	@make dev-setup -C geneweb_python

install:
	@make install -C geneweb_python

test:
	@make test -C geneweb_python

test-fast:
	@make test-fast -C geneweb_python

test-full:
	@make test-full -C geneweb_python

test-unit:
	@make test-unit -C geneweb_python

test-integration:
	@make test-integration -C geneweb_python

test-e2e:
	@make test-e2e -C geneweb_python

test-tdd:
	@make test-tdd -C geneweb_python

test-watch:
	@make test-watch -C geneweb_python

coverage:
	@make coverage -C geneweb_python

test-bf:
	@BACK_LOG=$$(mktemp -t backend-tests.XXXX.log); \
	FRONT_LOG=$$(mktemp -t frontend-tests.XXXX.log); \
	spin() { \
		pid=$$1; idx=0; \
		while kill -0 $$pid 2>/dev/null; do \
			idx=$$(( (idx + 1) % 4 )); \
			case $$idx in \
				0) ch='|';; \
				1) ch='/';; \
				2) ch='-';; \
				3) ch='\\';; \
			esac; \
			printf "\r   [%s] Running..." "$$ch"; \
			sleep 0.2; \
		done; \
		printf "\r%-30s\r" ""; \
	}; \
	echo "==> Running backend tests (coverage)"; \
	make coverage -C geneweb_python >$$BACK_LOG 2>&1 & \
	BACK_PID=$$!; \
	spin $$BACK_PID; \
	if wait $$BACK_PID; then \
		echo "✅ Backend tests passed"; \
		BACK_SUM=$$(grep -E '^TOTAL' $$BACK_LOG | tail -1); \
		if [ -n "$$BACK_SUM" ]; then \
			echo "   Coverage summary: $$BACK_SUM"; \
		else \
			tail -n 20 $$BACK_LOG; \
		fi; \
	else \
		echo "❌ Backend tests failed"; \
		tail -n 50 $$BACK_LOG; \
		echo "   (full log: $$BACK_LOG)"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "==> Running frontend tests (coverage)"; \
	(cd front && npm run test -- --watch=false --code-coverage >$$FRONT_LOG 2>&1) & \
	FRONT_PID=$$!; \
	spin $$FRONT_PID; \
	if wait $$FRONT_PID; then \
		echo "✅ Frontend tests passed"; \
		grep -E 'Statements|Branches|Functions|Lines' $$FRONT_LOG | head -4 | sed 's/^/   /' || true; \
	else \
		echo "❌ Frontend tests failed"; \
		tail -n 50 $$FRONT_LOG; \
		echo "   (full log: $$FRONT_LOG)"; \
		exit 1; \
	fi; \
	echo ""; \
	echo "Logs saved in:"; \
	echo "  backend  -> $$BACK_LOG"; \
	echo "  frontend -> $$FRONT_LOG"

lint:
	@make lint -C geneweb_python

format:
	@make format -C geneweb_python

type-check:
	@make type-check -C geneweb_python

quality:
	@make quality -C geneweb_python

ci-test:
	@make ci-test -C geneweb_python

ci-quality:
	@make ci-quality -C geneweb_python

tdd-red:
	@make test-tdd -C geneweb_python || true

tdd-green:
	@make test-green -C geneweb_python

tdd-refactor:
	@make test-refactor -C geneweb_python

dev-cycle:
	@make dev-cycle -C geneweb_python

re: fclean all

.PHONY: all clean fclean re test-bf
