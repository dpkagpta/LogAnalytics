# imorting libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model, metrics
from sklearn.model_selection import train_test_split


def coefficients(x, y):
    n=np.size(x)
    
    #calculating mean of x and y
    mean_x, mean_y = np.mean(x), np.mean(y)
    
    #calculating cross devaition sum of squares and sum of squares of x
    SS_xy = np.sum(x*y) - n*mean_x*mean_y
    SS_xx = np.sum(x*x) - n*mean_x*mean_x
    
    #calculating regression coefficients
    b_1 = SS_xy/SS_xx
    b_0 = mean_y - b_1*mean_x
    
    return(b_0, b_1)



def regression_line(x, y, b):
    plt.scatter(x, y, color = 'm', marker = '*', s=45)
    
    #predicted response vector
    y_pred = b[0] + b[1]*x
    plt.plot(x, y_pred, color='g')
    
    plt.xlabel = 'Size'
    plt.ylabel = 'Cost'
    
    plt.show()   
    


def main():
    
    #datasets
    x = np.array([1,2,3,4,5,6,7,8,9,10])
    y = np.array([300, 350,500,700,800,850,900,900,1000,1200])
    
    #estimating coefficients:
    b = coefficients(x, y)
    print('Estimated Coefficients:\nb_1 = {}, b_0 = {}'.format(b[0], b[1]))
    
    regression_line(x, y, b)



if __name__ == '__main__':
    main()


# # Multiple Linear Regression
boston_data = datasets.load_boston(return_X_y=False)


X = boston_data.data
y = boston_data.target

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 1)

reg = linear_model.LinearRegression()
reg.fit(x_train, y_train)


print('Coefficients:\n', reg.coef_)


print('Variance Score:\n', reg.score(x_test, y_test))

# plotting residuals in training data
plt.scatter(reg.predict(x_train), reg.predict(x_train) - y_train, color = 'green', s = 15, label = 'train_data')

# plotting residuals in test data
plt.scatter(reg.predict(x_test), reg.predict(x_test) - y_test, color= 'blue', s = 15, label = 'test_data')

## plotting line for zero residual error 
plt.hlines(y = 0, xmin = 0, xmax = 50, linewidth = 2) 

plt.legend(loc = 'upper right')
plt.title('residual errors')
plt.show()
