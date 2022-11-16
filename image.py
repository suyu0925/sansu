import cv2
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

img_cartoon = pipeline(Tasks.image_portrait_stylization,
                       model='damo/cv_unet_person-image-cartoon_compound-models')

img_cartoon_handdrawn = pipeline(Tasks.image_portrait_stylization,
                       model='damo/cv_unet_person-image-cartoon-handdrawn_compound-models')

img_artstyle = pipeline(Tasks.image_portrait_stylization,
                        model='damo/cv_unet_person-image-cartoon-artstyle_compound-models')

img_sketch = pipeline(Tasks.image_portrait_stylization,
                      model='damo/cv_unet_person-image-cartoon-sketch_compound-models')


def unet_cartoon(img_path, out_path):
    result = img_cartoon(img_path)
    cv2.imwrite(out_path, result[OutputKeys.OUTPUT_IMG])

def unet_cartoon_handdrawn(img_path, out_path):
    result = img_cartoon_handdrawn(img_path)
    cv2.imwrite(out_path, result[OutputKeys.OUTPUT_IMG])


def unet_artstyle(img_path, out_path):
    result = img_artstyle(img_path)
    cv2.imwrite(out_path, result[OutputKeys.OUTPUT_IMG])


def unet_sketch(img_path, out_path):
    result = img_sketch(img_path)
    cv2.imwrite(out_path, result[OutputKeys.OUTPUT_IMG])
