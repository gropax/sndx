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

          buildInputs = [
            pkgs.python312
            pkgs.poetry

            pkgs.ffmpeg
            pkgs.chromium
          ];

          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zeromq
          ];

          # Fix for opening tmux in nix-shell env
          SHELL= "${pkgs.bashInteractive}/bin/bash";

          # Allow pyppeteer to run nix-managed chromium
          CHROMIUM_PATH = "${pkgs.chromium}/bin/chromium";

          # Make the python virtual env local
          POETRY_VIRTUALENVS_IN_PROJECT = "1";

          shellHook = ''
            poetry install
          '';
          # To install kernel : python -m ipykernel install --user --name sndx --display-name "Python (sndx)"
        };
      });
}
