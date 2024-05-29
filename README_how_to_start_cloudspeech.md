# For at køre cloudspeech med object detection
Åben to terminaler med cloudspeech som root-directory.
1. **terminal (base)**: `base` anaconda environment (her skal der ikke gøres mere).
2. **terminal (dennis)**: Kør `conda activate dennis`.

Herefter skal følgende køres i denne rækkefølge:
1. I **terminal (dennis)** køres `python objectMedia.py`
2. I **terminal (base)** køres `python cloudspeech.py`

### For at køre det sidste mht. Menti opsummeringen
1. Smid det generede tekst ind i `final_read.txt`
2. I **terminal (base)** kør `python cloudspeech.py --final_read True`

# Hvad nu hvis robottens IP skifter?
Du står i root directory.
1. `cd robot`
2. `open *`
3. I de **5** scripts, skift alle IP-addresserne til den IP pepper siger højt.
4. Følg guiden *For at køre cloudspeech med object detection*.