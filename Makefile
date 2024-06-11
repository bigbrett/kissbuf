GEN_SOURCE = generated_serde.c
GEN_HEADER = generated_serde.h
MAIN_SOURCE = main.c
OUTPUT = a.out

# Rules
all: $(OUTPUT)

run: all
	./a.out

$(OUTPUT): $(MAIN_SOURCE) $(GEN_SOURCE) $(GEN_HEADER)
	gcc -o $(OUTPUT) $(MAIN_SOURCE) $(GEN_SOURCE)

$(GEN_SOURCE) $(GEN_HEADER): example.h
	python3 kissbuf.py

clean:
	rm -f $(OUTPUT) $(GEN_SOURCE) $(GEN_HEADER)

.PHONY: all clean

