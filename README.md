# Change songs through hand gestures
This project lets you control your playlist, which is playing at your laptop
without getting up from bed.  

There are five types of gestures / symbols supported
1. Play
2. Pause
3. Stop
4. Next 
5. Previous

# Platform supported
Currently Ubuntu 18.04 is only supported.
In future there are plans to extend support to other platforms.

# Installation
1. Run the **requirements.sh** using `./requirements.sh`
2. Install open vino from [here](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_linux.html).

# Running
-  Open VINO installtion is usually found **/opt/intel**.
So type the following command 
```
source /opt/intel/openvino/bin/setupvars.sh
```
-  Now in this repository go to Lazy_Change directory and type
```
python3 Lazy_Change.py
```

# Model optimizer 
To convert the trained model from  [here](https://github.com/deepanshu-yadav/open_vino_udacity/tree/master/train_script)
use the following command to convert the tensorflow .pb file to IR.
```
python3 /opt/intel/openvino/deployment_tools/model_optimizer/mo_tf.py --input_model /home/deepanshu/Downloads/tf_model.pb --output_dir /home/deepanshu/open_vino/udacity_project_custom_model/  --input_shape=[1,224,224,3] --data_type FP16
```

# Test Scripts
- For feeding your converted model into IE (Inference Engine) use the following command.
```  
python3 feed_network.py -m  model/tf_model.xml
 ```

-  Handling request with a test image

``` 
python3 inference_try.py -m model/tf_model.xml -i test_image.jpg -r S 
```


A Big Thank You to these guys 
1. Modified  [his](https://github.com/chaNcharge/PyTunes/)  code for GUI.
2. Took help from this [post](https://iosoft.blog/cam-display/) for displaying video feed in PyQt5.
3. Took songs from [him](https://github.com/yashshah2609/Emotion-Based-music-player).
4. Converted keras model to a freezed tensorflow model from [here](https://software.intel.com/en-us/forums/intel-distribution-of-openvino-toolkit/topic/820599).
5. Thank you [Udacity](www.udacity.com) for making such wonderful tutorials.
6. The best tutorial on Intel NCS is [here](https://www.pyimagesearch.com/2019/04/08/openvino-opencv-and-movidius-ncs-on-the-raspberry-pi/) .

