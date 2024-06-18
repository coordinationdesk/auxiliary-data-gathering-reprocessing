BEGIN {
      pre="";
      OFS=",";}
{
 printf("%s",  (NR==1 || pre!=$2? (NR>1? ORS:"")$2: "") OFS $1 ); 
 pre=$2;
}
END { print "" }
