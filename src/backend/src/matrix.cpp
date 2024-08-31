// matrix.cpp

#include "matrix.h"
#include <Arduino.h>
#include <stdlib.h>

Matrix createMatrix(int rows, int cols, int chainLength) {
    Matrix matrix;
    matrix.rows = rows;
    matrix.cols = cols;
    matrix.data = (uint16_t **)malloc(rows * sizeof(uint16_t *));
    for (int i = 0; i < rows; i++) {
        matrix.data[i] = (uint16_t *)malloc(cols * sizeof(uint16_t));
        for (int j = 0; j < cols; j++) {
            matrix.data[i][j] = 0x0000;
        }
    }
    // Config
    HUB75_I2S_CFG mxconfig(rows, cols, chainLength);
    matrix.panel = new MatrixPanel_I2S_DMA(mxconfig);
    matrix.panel->begin();
    return matrix;
}

void freeMatrix(Matrix matrix) {
    for (int i = 0; i < matrix.rows; i++) {
        free(matrix.data[i]);
    }
    free(matrix.data);
}

void changePixel(Matrix matrix, int row, int col, uint16_t color) {
    if (row >= 0 && row < matrix.rows && col >= 0 && col < matrix.cols) {
        matrix.data[row][col] = color;
        matrix.panel->drawPixel(col, row, color);
    }
}

uint16_t getPixel(Matrix matrix, int row, int col) {
    if (row >= 0 && row < matrix.rows && col >= 0 && col < matrix.cols) {
        return matrix.data[row][col];
    }
    return 0x0000;
}