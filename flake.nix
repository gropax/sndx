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
          name = "python-sndx";

          buildInputs = [
            pkgs.python314
            pkgs.python314Packages.venvShellHook
            pkgs.jupyter
          ];

          shellHook = ''
            export VIRTUAL_ENV=$PWD/.venv
            export PATH="$VIRTUAL_ENV/bin:$PATH"

            echo "Python ready $(python --version)"
            echo "venv active: $VIRTUAL_ENV"
            echo "To install python packages: pip install -r requirements.txt"
            echo "To launch Jupyter: jupyter notebook"
          '';
        };
      });
}
