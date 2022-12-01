
LANG=emfatic                       # set python for py150
DATADIR=../dataset/
LITFILE=no_lit
OUTPUTDIR=../save/codegpt-small-java
PRETRAINDIR=microsoft/CodeGPT-small-java        # microsoft/CodeGPT-small-py for py150
LOGFILE=completion_emfatic.log

python run_lm.py \
        --data_dir=$DATADIR \
        --lit_file=$LITFILE \
        --langs=$LANG \
        --output_dir=$OUTPUTDIR \
        --pretrain_dir=$PRETRAINDIR \
        --log_file=$LOGFILE \
        --model_type=gpt2 \
        --block_size=512 \
        --do_train \
        --gpu_per_node=1 \
        --learning_rate=8e-5 \
        --weight_decay=0.01 \
        --evaluate_during_training \
        --per_gpu_train_batch_size=2 \
        --per_gpu_eval_batch_size=4 \
        --gradient_accumulation_steps=4 \
        --num_train_epochs=15 \
        --logging_steps=100 \
        --save_steps=1000 \
        --seed=42 \
        --overwrite_output_dir \
        --not_pretrain