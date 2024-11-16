import cv2
import numpy as np
from PIL import Image

from facenet import Facenet

if __name__ == "__main__":
    model = Facenet()

    #while True:
        # image_1 = input('Input image_1 filename:')
        # try:
        #     image_1 = Image.open(image_1)
        # except:
        #     print('Image_1 Open Error! Try again!')
        #     continue

        # image_2 = input('Input image_2 filename:')
        # try:
        #     image_2 = Image.open(image_2)
        # except:
        #     print('Image_2 Open Error! Try again!')
        #     continue
        #
        # #probability = model.detect_image(image_1,image_2)
        # #print(probability)
        # image_1="img/g10.jpg"
        # image_1 = Image.open(image_1)
        # lr=model.detect_image(image_1,image_2)
        # print(lr)



    #使用 OpenCV 读取图像（这将返回一个 NumPy 数组）
    opencv_image = cv2.imread('facial_data/1000.jpg')
    image_1 = "1000.jpg"
    image_1 = Image.open(image_1)
    # #
    # # # 注意：OpenCV 读取的图像是 BGR 格式，而 PIL 使用的是 RGB 格式。
    # # # 因此，在转换之前，我们需要将图像从 BGR 转换为 RGB。
    rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
    rgb_image_2 = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
    # # # 将 NumPy 数组转换为 PIL 图像对象
    pil_image = Image.fromarray(rgb_image)
    pil_image_2=Image.fromarray(rgb_image_2)
    pl=model.detect_image(pil_image_2,image_1)
    print(pl)
    # #print(rgb_image,rgb_image_2)

    #lr=model.detect_image()
    #print(lr)

  #   #print(output1)
  #   # 将向量存储到 txt 文件中
  #   np.savetxt('vector.txt', output1)  # fmt='%d' 表示以整数格式存储
  #   # 从 txt 文件中读取数据
  #   loaded_vector = np.loadtxt('vector.txt', dtype=float)  # 指定数据类型为整数
  #   print(loaded_vector)


    #l1 = np.linalg.norm(output1 - output2, axis=1)
    #print(l1)
