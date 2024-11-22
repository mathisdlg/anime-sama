{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShellNoCC {
    name = "MassDL";

    nativeBuildInputs = with pkgs.buildPackages; [
        python3
        python3Packages.requests
        python3Packages.beautifulsoup4
        curl
    ];
}