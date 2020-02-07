
import argparse

import tensorflow as tf
from tensorflow.python.saved_model import utils as smutils
from tensorflow.python.saved_model import signature_constants
from tensorflow.python.saved_model import signature_def_utils
from tensorflow.python.saved_model import tag_constants
from onnx_tf.backend import prepare

import onnx
import torch
import torchvision

onnx_file = 'meta/owen.onnx'
meta_file = 'meta/unconfiged.pb'
export_dir = 'models/resnet18/1'


def export_onnx(model, dummy_input, file, input_names, output_names,num_inputs):
    torch.onnx.export(
        model,
        args=dummy_input,
        input_names=input_names,
        output_names=output_names,
        f=file
    )

    model = onnx.load(file)
    model = make_variable_batch_size(num_inputs, model)
    onnx.save(model, file)


def make_variable_batch_size(num_inputs, onnx_model):
    for i in range(num_inputs):
        onnx_model.graph.input[i].type.tensor_type.shape.dim[0].dim_param = 'batch_size'
    return onnx_model


def export_tf_proto(onnx_file, meta_file):
    model = onnx.load(onnx_file)
    print('\n\n model loaded \n\n')

    tf_rep = prepare(model, strict=False)
    print('\n\n model prepared \n\n')
    output_keys = tf_rep.outputs
    input_keys = tf_rep.inputs
    print('\n\n io keys extracted \n\n')

    tf_dict = tf_rep.tensor_dict
    input_tensor_names = {key: tf_dict[key] for key in input_keys}
    output_tensor_names = {key: tf_dict[key] for key in output_keys}
    print(f'\n\n {tf_dict} \n\n')
    print(f'\n\n {input_tensor_names} \n\n')
    print(f'\n\n {output_tensor_names} \n\n')

    tf_rep.export_graph(meta_file)
    print('\n\n export graph \n\n')

    return input_tensor_names, output_tensor_names


def export_for_serving(meta_path, export_dir, input_tensors, output_tensors):
    g = tf.Graph()
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
    graph_def = tf.GraphDef()

    with sess.as_default():
        with g.as_default():
            with open(meta_path, "rb") as f:
                graph_def.ParseFromString(f.read())

            tf.import_graph_def(graph_def, name="")

            tensor_info_inputs = {
                name: smutils.build_tensor_info(in_tensor) for name, in_tensor in input_tensors.items()
            }

            tensor_info_outputs = {
                name: smutils.build_tensor_info(out_tensor) for name, out_tensor in output_tensors.items()
            }

            prediction_signature = signature_def_utils.build_signature_def(
                inputs=tensor_info_inputs,
                outputs=tensor_info_outputs,
                method_name=signature_constants.PREDICT_METHOD_NAME
            )

            # predict_tensor_inputs_info = tf.saved_model.utils.build_tensor_info(jpegs) 
            # predict_tensor_scores_info = tf.saved_model.utils.build_tensor_info(net.discriminator_out)

            # prediction_signature = tf.saved_model.signature_def_utils.build_signature_def( 
            #     inputs={'images': predict_tensor_inputs_info}, 
            #     outputs={'scores': predict_tensor_scores_info},
            #     method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME
            # )

            print(tensor_info_inputs)
            print(tensor_info_outputs)
            print(signature_constants.PREDICT_METHOD_NAME)
            print(prediction_signature)

            builder = tf.saved_model.builder.SavedModelBuilder(export_dir)
            legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op') 
            print(legacy_init_op)
            builder.add_meta_graph_and_variables(
                sess,
                [tag_constants.SERVING],
                signature_def_map={"predict_images": prediction_signature},
                strip_default_attrs=True,
                clear_devices=True,
                legacy_init_op=legacy_init_op
            )
            builder.save()


def main(onnx_file, meta_file, export_dir):
    model = torchvision.models.resnet18(pretrained=True)
    img_input = torch.randn(1, 3, 224, 224)

    input_names = ['input_img']
    output_names = ['confidences']

    # Use a tuple if there are multiple model inputs
    dummy_inputs = img_input

    export_onnx(
        model, dummy_inputs, onnx_file,
        input_names=input_names,
        output_names=output_names,
        num_inputs=len(dummy_inputs)
    )
    
    input_tensors, output_tensors = export_tf_proto(
        onnx_file,
        meta_file
    )
    print('\n\n i/o and meta_file ran \n\n')
    export_for_serving(
        meta_file,
        export_dir,
        input_tensors,
        output_tensors
    )


if __name__ == "__main__":
    main(onnx_file, meta_file, export_dir)