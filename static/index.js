const modalWrapper = document.querySelector(".modals-wrapper");
if (modalWrapper){
    function displayModal(id){
        const modal = document.getElementById(id);
        modalWrapper.style.display = "flex";
        modal.style.display = "flex";

        const closeBtn = document.getElementById("close-modal");
        closeBtn.addEventListener("click", () => {
            modalWrapper.style.display = "none";
            modal.style.display = "none";
            document.querySelector("header").style.display = "";
            document.querySelector("footer").style.display = "";
        })
        document.querySelector("header").style.display = "none";
        document.querySelector("footer").style.display = "none";
    }
}

//Display the actions of the password card for mobile devices
const actions = document.querySelectorAll(".actions");
if (actions){
    actions.forEach(action =>{
        action.onclick = () =>{
            const links = action.querySelectorAll("a");
            links.forEach(link =>{
                link.style.display = "flex";
            })
            setTimeout(function(){
                links.forEach(link =>{
                    link.style.display = "none";
                })}
            ,3000)
        }
    })
}