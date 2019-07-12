import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib
import os
import matplotlib.pyplot as plt
import datetime

#tf.set_random_seed(777)  # for reproducibility
def pridict_stock_price(company_id):

    def MinMaxScaler(data):
        # 데이터 모든숫자들을 최소 값만큼 뺀다.
        numerator = data - np.min(data,0)
        # 최대값과 최소 값의 차이(A)를 구한다.
        denominator = np.max(data,0) - np.min(data,0)
        # 너무 큰 값이 나오지 않도록 나눈다
        # print("정규화값 : "+ str(numerator / (denominator + 1e-7)))
        return numerator / (denominator + 1e-7)

    # def reverse_min_max_scaling(price, testPredict):
        # print("")
        

    # LSTM과 Linear Regression 으로 해보기

    # Window Size
    win_size = 3
    # input dimension(시가, 고가, 저가, 종가, 거래량)
    data_dim=5
    # output dimension(예측값)
    output_dim=1
    # 각 셀의 출력 크기
    hidden_dim=10
    # 학습률
    learning_rate=0.01

    st=pd.read_csv('005930_20190711.csv')
    st2=st.drop(st.columns[[0,6]],axis=1)
    st2.to_csv('stock_prophet.csv', index=False)

    # Open,High,Low,Close,Volume
    xy = np.loadtxt('stock_prophet.csv', delimiter=',')
    # 역순(날짜순 배열)
    xy = xy[::-1]
    # Normalize(정규화)
    xy = MinMaxScaler(xy)

    # x값 - 전체
    x = xy
    # y값 - Close as label
    y = xy[:, [-1]] # 마지막 열이 정답(주식 종가)

    dataX = []
    dataY = []

    # window를 옮기며 sequence 길이만큼 data 저장
    for i in range(0, len(y) - win_size):
        _x = x[i:i + win_size]
        _y = y[i + win_size]  # 다음 종가
        # print(_x, "->", _y)
        dataX.append(_x)        # x는 window_size만큼 저장
        dataY.append(_y)        # y는 예측값 1개씩 저장

    # split to train and testing
    train_size = int(len(dataY) * 0.7)  # train set (70%)
    test_size = len(dataY) - train_size # test set (30%)

    trainX, testX = np.array(dataX[0:train_size]), np.array(dataX[train_size:len(dataX)])

    trainY, testY = np.array(dataY[0:train_size]), np.array(dataY[train_size:len(dataY)])

    # input placeholders
    # X는 sequence data이기 때문에 [batch size/sequence length/data dimension]
    X = tf.placeholder(tf.float32, [None, win_size, data_dim])
    # Y는 output이 하나만 나오기 때문에 [batch size/1]
    Y = tf.placeholder(tf.float32, [None, 1])

    # output 이전에 Fully-Connected 추가(size=hidden_dim)
        # LSTM cell 생성
    cell = tf.contrib.rnn.BasicLSTMCell(num_units=hidden_dim, state_is_tuple=True)
    # dynamic_rnn 함수를 통해 cell과 X를 넣어 output을 도출
    outputs, _states = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32)

    # Y예측값
        # 만든 output을 layers를 통해 fully_connected 하나 생성
        # outputs[:,-1] 를 통해 마지막 것만 쓸 것임을 명시, output_dim=1 (최종출력 1개)
    Y_pred = tf.contrib.layers.fully_connected(
        outputs[:,-1], output_dim, activation_fn=None)
        
    # cost/loss
        # Mean squared Error(평균제곱오차) = (pred_val - real_val)^2 , 작을수록 예지력 상승
    loss = tf.reduce_sum(tf.square(Y_pred - Y)) # sum of the squares
    # optimizer(최적화), loss function의 결괏값을 최소화하는 모델의 인자를 찾는 것
    # 현존하는 Optimizer중 가장 성능이 좋은 Adam Optimizer 사용
        # Adam : Momentum과 AdaGrad를 섞은 기법 (학습의 갱신 강도 적응적 조정)
                # Momentum : 운동량 의미, 기울기가 음수이면 속도 증가(내리막), 반대는 오르막
                # AdaGrad : 학습률 감소 적용 (학습 진행시마다 갱신 정도 감소)
    optimizer = tf.train.AdamOptimizer(learning_rate)
    # optimizer가 minimize
    train = optimizer.minimize(loss)

    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    # 학습시키기
    for i in range(1000):
        _, l = sess.run([train, loss],feed_dict={X: trainX, Y: trainY})   # trainX, trainY를 넣어 학습시킴
        # print(i, l)

    # textX 값을 통해 Y_pred 값을 예측해 봄
    testPredict = sess.run(Y_pred, feed_dict={X: testX})

    # import matplotlib.pyplot as plt
    # matplotlib.use('Agg')

    # plt.plot(testY)         # true
    # plt.plot(testPredict)   # 예측한 값
    # fig=plt.gcf()
    # plt.show()




    ##############################################
    # now = datetime.datetime.now()
    # date = now.strftime('%Y%m%d')

    # img_name = "./img/predict/" + company_id + ".png"
    # img_name = "./img/predict/" + company_id + '_' + date + ".png"
    # print(img_name)
    # fig.savefig(img_name)


    return 5000

# pridict_stock_price("005930")