
var changes = document.getElementsByClassName("change");
for (let i = 0 ; i < changes.length;++i) 
{
    let change = changes[i];
    if(change.innerHTML.charAt(0) == '+'){
        change.style.color = "green";
    }
    else if(change.innerHTML.charAt(0) == '-'){
        change.style.color = "red";
    }
}