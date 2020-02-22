# Model optimizer command 
```python3 /opt/intel/openvino/deployment_tools/model_optimizer/mo_tf.py --input_model /home/deepanshu/Downloads/tf_model.pb --output_dir /home/deepanshu/open_vino/udacity_project_custom_model/  --input_shape=[1,224,224,3] --data_type FP16```

# feeding model into IE test script
```  python3 feed_network.py -m  model/tf_model.xml ```

# handling request with an image test script

``` python3 inference_try.py -m model/tf_model.xml -i test_image.jpg -r S ```