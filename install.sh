#! /usr/bin/env bash

pip3 install -r requirements.txt && \
    python3 setup.py bdist_wheel && \
        pip3 install dist/*.whl

if [[ -d $HOME/.local/share/applications ]]; then
    cp compresspdf.desktop $HOME/.local/share/applications/
else
    sudo cp compresspdf.desktop /usr/share/applications/
fi

