#!/usr/bin/env bash

function replace_ipfs_address() {
    echo "Type the address of your IPFS node (eg http://localhost:5001)";
    read IPFS_ADDRESS;
    template="http://ipfs:5001";
    sed -i "s!$template!$IPFS_ADDRESS!" "$1";
}

function replace_exec() {
    template="EXECUTABLE_REPLACE";
    sed -i "s@$template@$2@" "$1";
}

function replace_param() {
    template="INSTANCE_$1_REPLACE";
    echo "Give INSTANCE_$1";
    read INPUT;
    sed -i "s/$template/$INPUT/" "$2";
}

if ! command -v git; then
    echo "Git is not installed. Setup cannot continue";
    exit 1;
fi

mkdir .local
cd ~/.local;
git clone https://github.com/a-manga-thing/instance;
mv instance mangaloid;
cd mangaloid;
git checkout setup
git pull

if [[ -f docker-compose.yml || -f mangaloid.service || -f run.sh ]]; then
    echo "Looks like you have already finished an installation. This might overwrite stuff. Continue ? [y/n]";
    read INPUT;
    if [[ $INPUT != "y" ]]; then
        exit 0;
    fi
fi

INSTALLATION_METHOD="";
INIT_SYSTEM=$(ps --no-headers -o comm 1);

echo "Select installation method:
[1] Docker (Recommended)
[2] Pip System-wide installation
[3] No Installation (Run from folder)";
while [[ "1" ]]; do
    read INPUT;
    case $INPUT in
        1)
            INSTALLATION_METHOD="docker";
            INIT_SYSTEM="docker";
            break;
            ;;
        2)
            INSTALLATION_METHOD="pip";

            break;
            ;;
        3)
            INSTALLATION_METHOD="none";
            break;
            ;;
        *)
            echo "Wrong input. Try again";
            ;;
    esac
done

echo "Select IPFS setting:
[1] Managed by instance (Recommended)
[2] External
";
while [[ "1" ]]; do
    read INPUT;
    case $INPUT in
        1)
            break;
            ;;
        2)
            case $INIT_SYSTEM in
                "systemd")
                    cp inits/mangaloid.service.template mangaloid.service
                    replace_ipfs_address mangaloid.service;
                    ;;
                "docker")
                    cp inits/docker-compose.yml.template docker-compose.yml
                    replace_ipfs_address docker-compose.yml;
                    for ((i=25;i<=41;i++)); do
                        line=$(sed $i"q;d" docker-compose.yml);
                        newline="#$line";
                        sed -i $i"s!.*!$newline!" docker-compose.yml;
                    done
                    ;;
                "init")
                    echo "SysV isn't really supported yet. Sorry...";
                    exit 1;
                    ;;
            esac
            break;
            ;;
        *)
            echo "Wrong input. Try again";
            ;;
    esac
done

params=("NAME" "ADDRESS" "OPERATOR" "DESCRIPTION");
case $INIT_SYSTEM in
    "docker")
        for i in "${params[@]}"; do 
            replace_param "$i" "docker-compose.yml";
        done
        ;;
    "systemd")
        for i in "${params[@]}"; do 
            replace_param "$i" "mangaloid.service";
        done
        ;;
    "init")
        for i in "${params[@]}"; do 
            replace_param "$i" "sysv-run.sh";
        done
        ;;
esac

case $INSTALLATION_METHOD in
    "docker")
        if ! command -v docker-compose; then
            echo "docker-compose is not installed. Setup cannot continue";
            exit 1;
        fi
        echo "The docker-compose.yml file is located in ~/.local/mangaloid";
        docker-compose up -d;
        exit 0;
        ;;
    "pip")
        pip install .
        location=$(python -c "import os, site; print(os.path.join(site.USER_BASE, 'Scripts' if os.name == 'nt' else 'bin'))");
        executable="$location/mangaloid-instance";
        ;;
    "none")
        executable="$HOME/.local/mangaloid/run.sh"
        ;;
esac

case $INIT_SYSTEM in
    "systemd")
        replace_exec mangaloid.service "$executable";
        sed -i "s@%h@$HOME@" mangaloid.service;
        sed -i "s@REPLACE_USER@$USER@" mangaloid.service;
        echo "Enabling systemd service...";
        sudo cp mangaloid.service /etc/systemd/system;
        sudo systemctl daemon-reload
        sudo systemctl enable --now mangaloid.service;
        sudo systemctl status mangaloid.service
        ;;
    "init")
        replace_exec sysv-run.sh "$executable";
        ;;
esac