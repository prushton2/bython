{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";
  };

  outputs = {self, nixpkgs}:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };

    bython-prushton = pkgs.python313Packages.buildPythonPackage rec {
      pname = "bython_prushton";
      version = "1.3.1";
      format = "pyproject";

      buildInputs = [
        pkgs.python313Packages.hatchling
      ];

      src = pkgs.python313Packages.fetchPypi{
        inherit version pname;
        sha256 = "sha256-nivSLT650L6QddLFsrhYzQhgXGGqQ1zT49BLK2Dr2f0=";
      };
    };
  in
  {
    devShells.x86_64-linux.default = pkgs.mkShell {
      packages = with pkgs; [
        python313
        python313Packages.colorama
        python313Packages.hatchling
        python313Packages.build
        python313Packages.twine
      ];
    };

    packages.${system} = {
      default = bython-prushton;
      bython-prushton = bython-prushton;
    };

    legacyPackages.${system} = {
      python313Packages = {
        bython-prushton = bython-prushton;
      };
    };
    
  };
}