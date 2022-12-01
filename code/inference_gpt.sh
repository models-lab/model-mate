export CUDA_VISIBLE_DEVICES=0
LANG=emfatic                       # set python for py150
DATADIR=../dataset/
LITFILE=no_lit
OUTPUTDIR=../save/codegpt-small-java
PRETRAINDIR=microsoft/CodeGPT-small-java        # microsoft/CodeGPT-small-py for py150
LOGFILE=completion_emfatic_eval.log

python -u run_lm.py \
        --data_dir=$DATADIR \
        --lit_file=$LITFILE \
        --langs=$LANG \
        --output_dir=$OUTPUTDIR \
        --pretrain_dir=$PRETRAINDIR \
        --log_file=$LOGFILE \
        --model_type=gpt2 \
        --block_size=512 \
        --do_eval \
        --per_gpu_eval_batch_size=16 \
        --logging_steps=100 \
        --seed=42