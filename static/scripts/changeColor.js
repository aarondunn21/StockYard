
var times = document.getElementsByClassName("change");
for (let i = 0 ; i < times.length;++i) 
{
    let time = times[i];
    if(time.innerHTML.charAt(0) == '+'){
        time.style.color = "green";
    }
    else if(time.innerHTML.charAt(0) == '-'){
        time.style.color = "red";
    }
}