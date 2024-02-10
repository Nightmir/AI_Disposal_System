import os
from pathlib import Path
import tensorflow as tf

img_link = list(Path("garbage_dataset_large").glob(r'**/*.jpg'))

count_num = 0
for lnk in img_link:
    binary_img = open(lnk, 'rb')
    find_img = tf.compat.as_bytes('JFIF') in binary_img.peek(10)  # The JFIF is a JPEG File Interchange Format (JFIF). It is a standard which we gauge if an image is corrupt or substandard
    if not find_img:
        count_num += 1
        os.remove(str(lnk))
print('Total %d pcs image delete from Dataset' % count_num)
# this should help you delete the bad encoded
