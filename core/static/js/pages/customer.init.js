function editCustomer(e){var e=e,t=document.getElementById("username-"+e).innerText,n=document.getElementById("phone-"+e).innerText,o=document.getElementById("email-"+e).innerText,l=document.getElementById("address-"+e).innerText,d=document.getElementById("wallet_balance-"+e).getAttribute("data-id"),a=document.getElementById("rating-"+e).innerText;document.getElementById("username").value=t,document.getElementById("phone").value=n,document.getElementById("email").value=o,document.getElementById("address").value=l,document.getElementById("rating").selectedIndex=a-1,document.getElementById("wallet_balance").value=d,document.getElementById("uid").value=e}function sweetDelete(o){console.log("id"+o);const l=document.querySelector("[name=csrfmiddlewaretoken]").value;Swal.fire({title:"Are you sure?",text:"You won't be able to revert this!",icon:"warning",showCancelButton:!0,confirmButtonText:"Yes, delete it!",cancelButtonText:"No, cancel!",confirmButtonClass:"btn btn-success mt-2",cancelButtonClass:"btn btn-danger ms-2 mt-2",buttonsStyling:!1}).then(function(e){if(e.isConfirmed){Swal.fire({title:"Deleted!",text:"Your record has been deleted.",icon:"success"});const t=new XMLHttpRequest,n=new FormData;n.append("id",o),n.append("deleteCustomer","deleteCustomer");t.open("POST","/ecommerce/customers"),t.setRequestHeader("X-CSRFToken",l),t.send(n),t.onload=()=>{window.location.reload()}}else Swal.fire({title:"Cancelled",text:"Your imaginary file is safe :)",icon:"error"})})}