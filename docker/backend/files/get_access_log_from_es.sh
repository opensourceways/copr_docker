#/bin/bash

print_help()
{
    echo "usage $0 -i [es ip] -p [es port] -u [es username] -P [es password] -o [output file]"
    exit 0
}

### main ###

while getopts 'i:p:u:P:o:h' OPT; do
    case $OPT in
        i) IPADDR="$OPTARG";;
        p) PORT="$OPTARG";;
        P) PASSWD="$OPTARG";;
        u) USER="$OPTARG";;
        o) FILE="$OPTARG";;
        h) print_help;;
        ?) print_help;;
    esac
done

if [ -z $USER ] || [ -z $IPADDR ] || [ -z $PORT ] || [ -z $PASSWD ] || [ -z $FILE ];then
    print_help
fi

TMP=$(mktemp)

# do urlencode
PASSWD=$(echo -n $PASSWD|jq -sRr @uri)
# need install jq and elasticdump firstly
NODE_TLS_REJECT_UNAUTHORIZED=0 elasticdump --input=https://$USER:$PASSWD@$IPADDR:$PORT  --output=$TMP --type=data --limit 1000 --searchBody '{"query": {"bool":{"must":[{"term":{ "kubernetes.labels.component.keyword": "copr-backend"}},{ "term":{"kubernetes.container_name.keyword": "httpd"}}, {"term":{"kubernetes.namespace_name.keyword": "fedora-copr-prod"}}]}}}' --overwrite &&
cat $TMP | jq '._source.log' > $FILE &&
[ -f $TMP ] && rm -f $TMP