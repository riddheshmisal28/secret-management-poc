docker run --rm `
  -v "${PWD}:/work" `
  -w /work `
  -e SOPS_AGE_KEY_FILE=/work/secrets/age-key.txt `
  secret-tools-sops `
  decrypt `
  --output /work/.env `
  /work/secrets/secrets.enc.env

docker compose up --build