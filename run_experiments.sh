for entry in "yaml_experiments"/*
do
  kubectl apply -f $entry
  echo "$entry"
done