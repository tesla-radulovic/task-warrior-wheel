{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [
    (pkgs.python312.withPackages (ps: with ps; [
      flask
      tasklib
    ]))
    pkgs.nodejs_22
  ];
}
