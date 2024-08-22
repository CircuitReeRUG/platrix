// matrix.h

#ifndef MATRIX_H
#define MATRIX_H

#include <stdint.h>
#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>

struct Matrix {
    int rows;
    int cols;
    uint16_t **data;
    MatrixPanel_I2S_DMA *panel;
};

Matrix createMatrix(int rows, int cols, int chainLength);
void freeMatrix(Matrix matrix);
void changePixel(Matrix matrix, int row, int col, uint16_t color);
uint16_t getPixel(Matrix matrix, int row, int col);

#endif
