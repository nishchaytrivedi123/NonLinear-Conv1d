# -*- coding: utf-8 -*-
"""1106924_con1d_reg.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LXbU5du8T9_HU5hHAVEMpUc3EUDDq5ad
"""



from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

import numpy as np

import matplotlib._color_data as mcd
import random

dataset = pd.read_csv('/content/drive/My Drive/Colab Notebooks/housing.csv')
dataset = dataset.dropna()
dataset.head(10)
dataset.to_csv('/content/drive/My Drive/Colab Notebooks/data.csv')





axSubPlt = []

fig, subPlotObj = plt.subplots(10)
fig.suptitle('Housing Features')
for i in range(10):
  axSubPlt.append(subPlotObj[i])

name_list = []

for i in dataset:
  name_list.append(str(i))
  
def random_color():
    rgba=(random.random(),random.random(),random.random())
    return rgba

numbers = [i for i in range(19)]

for i in range(10):
  axSubPlt[i].plot(numbers, dataset.iloc[:,i][0:19], color = random_color())
  axSubPlt[i].legend([name_list[i]])

plt.savefig('books_read.png')



Y = dataset['median_house_value']

X = dataset.loc[:,'longitude':'median_income']

X.shape

Y.shape

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size= 0.3, random_state = 2003)

x_train_np = x_train.to_numpy()
y_train_np = y_train.to_numpy()

x_test_np = x_test.to_numpy()
y_test_np = y_test.to_numpy()


# print("There are " + str(x_train.size) + " training entries and "+  str(x_test.size) + " testing entries ")

import torch

from torch.nn import Conv1d

from torch.nn import MaxPool1d

from torch.nn import Flatten

from torch.nn import Linear

from torch.nn.functional import relu

from torch.utils.data import DataLoader, TensorDataset

import time

class CnnRegressor(torch.nn.Module):
  def __init__(self, batch_size, inputs, outputs):
    super(CnnRegressor, self).__init__()
    self.batch_size = batch_size
    self.inputs = inputs
    self.outputs = outputs

    self.input_layer = Conv1d(inputs, batch_size, 1)

    self.max_pooling_layer = MaxPool1d(1)

    self.max_pooling_layer1 = MaxPool1d(1)

    self.conv_layer = Conv1d(batch_size, 64, 1)

    # self.conv_layer1 = Conv1d(512, 256, 1)

    self.flatten_layer = Flatten()

    self.linear_layer = Linear(64, 32)

    self.output_layer = Linear(32, outputs)

  def feed(self, input):
    input = input.reshape((self.batch_size, self.inputs,1))
    output = relu(self.input_layer(input))

    output = self.max_pooling_layer(output)

    output = relu(self.conv_layer(output))

    output = self.max_pooling_layer1(output)

    # output = relu(self.conv_layer1(output))

    output = self.flatten_layer(output)

    output = self.linear_layer(output)

    output = self.output_layer(output)
    return output

from torch.optim import SGD, Adam

from torch.nn import L1Loss

!pip install pytorch-ignite

from ignite.contrib.metrics.regression.r2_score import R2Score

batch_size = 64
# print(X.shape[1])
model = CnnRegressor(batch_size, X.shape[1], 1)

model.cuda()

torch.save(model, '/content/drive/My Drive/Colab Notebooks/1106924_1dconv_reg.pt')

torch.load('/content/drive/My Drive/Colab Notebooks/1106924_1dconv_reg.pt')
def model_loss(model, dataset, train = False, optimizer = None):
  performance = L1Loss()
  score_metric = R2Score()

  avg_loss = 0
  avg_score = 0
  count = 0

  for input, output in iter(dataset):
    predections = model.feed(input)

    loss = performance(predections, output)

    score_metric.update([predections, output])
    score = score_metric.compute()

    if(train):
      optimizer.zero_grad()

      loss.backward()

      optimizer.step()
    
    avg_loss += loss.item()

    avg_score += score
    count += 1

  return avg_loss / count, avg_score / count

epochs = 500

# optimizer = SGD(model.parameters())

optimizer = Adam(model.parameters())  

# optimizer = Adam(model.parameters(), lr=0.0001)

inputs = torch.from_numpy(x_train_np).cuda().float()
outputs = torch.from_numpy(y_train_np.reshape(y_train_np.shape[0],1)).cuda().float()

tensor = TensorDataset(inputs, outputs)

loader = DataLoader(tensor,batch_size, shuffle=True, drop_last=True)

start_time = time.time()

list_loss = []

list_r2 = []

for epoch in range(epochs):
  avg_loss, avg_r2_score = model_loss(model, loader, train=True, optimizer=optimizer)
  list_r2.append(avg_r2_score)
  list_loss.append( avg_loss)
  print("Epoch " + str(epoch + 1) + ":\n\tLoss = " + str(avg_loss) + "\n\tR^2 Score = " + str(avg_r2_score))

end_time = time.time()
plt.plot(list_loss)
plt.plot(list_r2)
plt.show()

# plt1.show()
print("Time taken to train this model with "+str(epochs)+ " epochs is: "+ str(end_time-start_time) + "sec")

inputs = torch.from_numpy(x_test_np).cuda().float()
outputs = torch.from_numpy(y_test_np.reshape(y_test_np.shape[0],1)).cuda().float()

tensor = TensorDataset(inputs, outputs)

loader = DataLoader(tensor,batch_size, shuffle=True, drop_last=True)

avg_loss, avg_r2_score = model_loss(model, loader)

print("Loss = " + str(avg_loss) + "\nR^2 Score = " + str(avg_r2_score))