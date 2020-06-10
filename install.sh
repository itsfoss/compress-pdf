#! /usr/bin/env bash

pip3 install -r requirements.txt && \
    python3 setup.py bdist_wheel && \
        pip3 install dist/*.whl

sudo mkdir -p /usr/share/itsfoss/resources/compress-pdf
sudo cp resources/*.png /usr/share/itsfoss/resources/compress-pdf/

if [[ -d $HOME/.local/share/applications ]]; then
    cp compresspdf.desktop $HOME/.local/share/applications/
else
    sudo cp compresspdf.desktop /usr/share/applications/
fi

