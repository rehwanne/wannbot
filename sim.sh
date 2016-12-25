#!/bin/bash
set -o nounset
set -o errexit

cmd="$1"
shift 1
text="$@"

post_data="channel_id=cniah6qa73bjjjan6mzn11f4ie&channel_name=test-channel&command=${cmd}&response_url=not+supported+yet& team_domain=praemandatum&team_id=rdc9bgriktyx9p4kowh3dmgqyc&text=${text}&token=xr3j5x3p4pfk7kk6ck7b4e6ghh& user_id=c3a4cqe3dfy6dgopqt8ai3hydh&user_name=stoneballs"

curl -s -X POST -d "$post_data" http://localhost:5000 | python -m json.tool
