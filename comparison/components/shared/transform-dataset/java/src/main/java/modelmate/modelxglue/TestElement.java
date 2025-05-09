package modelmate.modelxglue;

import com.fasterxml.jackson.annotation.JsonProperty;

public class TestElement {
        
        @JsonProperty
        private String ids;
        @JsonProperty
        private String owner;
        @JsonProperty
        private String target;
        @JsonProperty
        private String emfatic;

        public TestElement(String id, String owner, String target, String emfatic) {
                this.ids = id;
                this.owner = owner;
                this.target = target;
                this.emfatic = emfatic;
        }

}
