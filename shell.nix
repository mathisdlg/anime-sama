{ pkgs ? import <nixpkgs> {} }:
let
    pythonModules = with pkgs.python3Packages; [
        requests
        beautifulsoup4
        pycurl
        django
    ];
in pkgs.mkShellNoCC {
    name = "MassDL";

    nativeBuildInputs = with pkgs.buildPackages; [
        python3
        curl
    ] ++ pythonModules;
}