# Multimodal Alzheimer Detection

This project provides a modular Python pipeline for early Alzheimer’s disease screening. It supports two data modes:

- Speech/audio screening with feature extraction, LSTM, Transformer, and dense models
- Kaggle tabular dementia prediction with a dense neural network baseline
- Training, evaluation, and inference scripts
- A Streamlit demo for speech uploads

## Project layout

- `src/alzheimers_speech/`: package code
- `configs/`: experiment configuration files
- `models/`: saved model artifacts
- `data/`: expected dataset layout
- `app.py`: Streamlit demo entrypoint

## Data expectations

Speech mode expects audio files and a CSV metadata file with at least these columns:

- `recording_id`
- `audio_path`
- `label`

Optional columns such as `age`, `sex`, `education`, and `task_type` can be added and will be used when present.

Kaggle tabular mode uses the dataset from [shashwatwork/dementia-prediction-dataset](https://www.kaggle.com/datasets/shashwatwork/dementia-prediction-dataset), which contains a single CSV file and no audio. Use [configs/kaggle_dementia.yaml](configs/kaggle_dementia.yaml) and place the Kaggle CSV at `data/raw/dementia_dataset.csv`.

For ADReSS / ADReSSo / DementiaBank speech datasets:

- Access is controlled by the data owners and cannot be auto-downloaded without approval.
- After you receive and extract the dataset, place it under `data/raw/adress/`.
- Build a metadata CSV from folder labels and then train with:

```bash
python -m src.alzheimers_speech.import_speech_dataset --dataset-root data/raw/adress --output-csv data/raw/metadata_adress.csv
python -m src.alzheimers_speech.train --config configs/adress.yaml
```

The importer infers labels from folder names using common hints:

- AD / Dementia class: `ad`, `cd`, `dementia`, `alz`
- Control class: `cc`, `control`, `healthy`, `non-ad`

## Setup

1. Create a Python 3.10+ environment.
2. Install dependencies from `requirements.txt`.
3. Place your dataset under `data/raw/` or update the config file you are using.

To download the Kaggle dementia dataset directly, configure Kaggle API credentials and run:

```bash
python -m src.alzheimers_speech.download_kaggle --output-dir data/raw
```

## Training

Run the training pipeline with:

```bash
python -m src.alzheimers_speech.train --config configs/default.yaml
```

For the Kaggle dementia CSV, use:

```bash
python -m src.alzheimers_speech.train --config configs/kaggle_dementia.yaml
```

For ADReSS/ADReSSo speech training after local extraction:

```bash
python -m src.alzheimers_speech.train --config configs/adress.yaml
```

## Data preview

Check your metadata, split sizes, and missing audio files before training:

```bash
python -m src.alzheimers_speech.prepare_data --config configs/default.yaml
```

For the Kaggle CSV:

```bash
python -m src.alzheimers_speech.prepare_data --config configs/kaggle_dementia.yaml
```

## Evaluation

```bash
python -m src.alzheimers_speech.evaluate --config configs/default.yaml
```

Kaggle CSV evaluation:

```bash
python -m src.alzheimers_speech.evaluate --config configs/kaggle_dementia.yaml
```

## Inference

```bash
python -m src.alzheimers_speech.predict --audio path/to/audio.wav --config configs/default.yaml
```

For tabular Kaggle predictions, use `predict_tabular` from Python or I can wire a CSV upload UI next.

## Streamlit demo

```bash
streamlit run app.py
```

## Notes

- The included models are designed as a strong starting point and should be retrained on a clinically curated dataset.
- For speech data, validate performance with subject-level splits to avoid data leakage.
- The Kaggle dementia CSV is a tabular baseline, not a speech/audio dataset.