{
  description = "Python project to extract sound from web streams";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let 
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells.default = pkgs.mkShell {
          name = "sndx";
          venvDir = "./.venv";

          buildInputs = [
            pkgs.python312Packages.python
            pkgs.python312Packages.venvShellHook
          ];

          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zeromq
          ];

          #postVenvCreation = ''
          #  unset SOURCE_DATE_EPOCH
          #'';
          #postShellHook = ''
          #  unset SOURCE_DATE_EPOCH
          #'';
        };
      });
}
