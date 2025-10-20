{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";
  };

  outputs = {self, nixpkgs}:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in
  {
    devShells.x86_64-linux.default = pkgs.mkShell {
      packages = with pkgs; [
        python313
        python313Packages.colorama
      ];
    };
  };
}