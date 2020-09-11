for entry in "yaml_experiments"/*
do
  kubectl delete -f $entry
  echo "$entry"
done