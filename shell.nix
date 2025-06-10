let
  pkgs = import (
    fetchTarball "https://github.com/NixOS/nixpkgs/archive/refs/tags/25.05.tar.gz"
  ) {};
in pkgs.mkShell {
    packages = [
        (pkgs.python313.withPackages (python-pkgs: with python-pkgs; [
            colorama
        ]))
    ];
}