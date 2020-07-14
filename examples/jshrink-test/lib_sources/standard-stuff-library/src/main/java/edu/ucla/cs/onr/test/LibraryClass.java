package edu.ucla.cs.onr.test;

public class LibraryClass {

	private static final String x="NOT ACCESSIBLE";

	public LibraryClass(){}

	public int getNumber(){
		String temp = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB";
		System.out.println("getNumber touched");
		int i=0;
		i++;
		i*=10;
		return i;
	}

	public int untouchedGetNumber(){
		String temp = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
		System.out.println("untouchedGetNumber touched");
		int i=0;
		i++;
		i*=10;
		return i;
	}

	private int privateUntouchedGetNumber(){
		String temp = "Lorem ipsum dolor sit amet, prima adipisci et est, mel et purto duis ludus." +
			" Vix mollis ancillae te. Eu pro purto soleat consetetur. Vix eripuit reprehendunt id." +
			" Audire vidisse aperiri eu sed, incorrupte scripserit signiferumque ad est, omnes " +
			"platonem ex sea. His libris invenire eu. Falli tractatos qui ea, officiis recusabo " +
			"convenire ea eos, pri hinc oratio delenit an.Omnesque conceptam appellantur ei vel, an " +
			"quo possim audiam. Consulatu vituperatoribus nam ea, eos an paulo copiosae. Paulo dolor " +
			"ei his, eam eu minim partem, saepe putent concludaturque vis ex. Nibh consulatu " +
			"interpretaris pri id, ut urbanitas delicatissimi mei. Te vim aperiam principes assueverit," +
			" ea purto imperdiet dissentiunt eos, ex autem mucius iuvaret quo.In his nibh partiendo " +
			"ocurreret. Probatus corrumpit molestiae ei ius. In qui dictas doctus atomorum, illum " +
			"vocent cotidieque no sit, ne mei discere facilis lucilius. Mei efficiendi reformidans " +
			"theophrastus ea, no vis erat novum laoreet, atqui euripidis mea cu. Ex omnes omnesque cum." +
			"An eam prima dicta eligendi, dictas option repudiandae no nam. Nisl vero ei duo. Pericula " +
			"posidonium eu pri, et ius tale constituam. Rebum veritus in ius. Ut mei dicit repudiandae, " +
			"vim an primis propriae efficiendi, et quas debitis laboramus eam. Cum elitr principes ei.Prima" +
			" nulla eligendi ex eum, saperet debitis ullamcorper et cum, ut ius autem denique expetendis." +
			" Nobis adversarium an qui, nec no melius iuvaret. Eum mundi tantas eu, novum aperiam pri ei." +
			" Eam reprimique neglegentur delicatissimi eu, molestie iudicabit ius ne, ullum dolore animal" +
			" ei cum. Dolorum nusquam eleifend et pri, in errem mentitum sed.";
		System.out.println("privateUntouchedGetNumber touched");
		int i=0;
		i++;
		i*=10;
		return i;
	}
}
