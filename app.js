document.addEventListener(
    "DOMContentLoaded",
    function()
    {


        console.log(
            "MY TV APP interface chargée"
        );



        /*
        Aperçu des images
        pour logo et couverture
        */

        const imageInputs =
        document.querySelectorAll(
            'input[type="file"]'
        );



        imageInputs.forEach(
            function(input)
            {


                input.addEventListener(
                    "change",
                    function()
                    {


                        const file =
                        this.files[0];



                        if(
                            file &&
                            file.type.startsWith("image")
                        )
                        {

                            console.log(
                                "Image sélectionnée : "
                                + file.name
                            );

                        }


                    }
                );


            }
        );





        /*
        Confirmation avant action importante
        */

        const forms =
        document.querySelectorAll(
            "form"
        );



        forms.forEach(
            function(form)
            {

                form.addEventListener(
                    "submit",
                    function()
                    {

                        console.log(
                            "Envoi du formulaire..."
                        );


                    }
                );


            }
        );




    }
);