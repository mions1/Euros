<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html>
	<head>
	
	
<script type="text/javascript">
	//19 paesi
	paesi=new array (
		"Austria",
		"Belgio",
		"Cipro",
		"Estonia",
		"Finlandia",
		"Francia",
		"Germania",
		"Grecia",
		"Irlanda",
		"Italia",
		"Lettonia",
		"Lituania",
		"Lussemburgo",
		"Malta",
		"Olanda",
		"Portogallo",
		"Slovacchia",
		"Slovenia",
		"Spagna"
		);
	monete=new array (
		"0,01",
		"0,02",
		"0,05",
		"0,10",
		"0,20",
		"0,50",
		"1",
		"2"
		);
	estensione="jpg";
	</script>
	
	</head>
	<body>
		<table>
			
<script type="text/javascript">
				for (i=0;i<paesi.length;i++) {
					document.write("<tr>");
					for(j=0;j<monete.length;j++) {
						document.write("<td>");
						document.write( "<img src='"+paesi[i]+"\\"+monete[j]+"."+estensione+"'>" );
						document.write("</td>");
					}
					document.write("</tr>");
				}
			</script>
		</table>
	</body>
</html>