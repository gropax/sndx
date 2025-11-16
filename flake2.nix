{
  description = "Python project to extract sound from web streams";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let 
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            (final: prev: {
              pythonEnv = prev.python3.withPackages (ps: [
                ps.jupyter
                #ps.numpy
                #ps.pandas
                #ps.matplotlib
              ]);
            })
          ];
        };
      in {
        devShells.default = pkgs.mkShell {
          name = "python-env";
          buildInputs = [
            pkgs.jupyter
            pkgs.pythonEnv
          ];

          shellHook = ''
            echo "Python ready $(python --version)"
            echo "To launch Jupyter: jupyter notebook"
          '';
        };
      });
}
