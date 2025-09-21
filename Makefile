CXX = gcc
CXXFLAGS = -Wall -Wextra -g
TARGET = procgen
SRC = procgen.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all clean verbose
