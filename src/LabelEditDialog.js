import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import withRoot from './withRoot';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import graphvizVersions from './graphviz-versions.json';
import packageJSON from '../package.json';
import versions from './versions.json';
import Button from '@material-ui/core/Button';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

const styles = theme => ({
  title: {
    display: 'flex',
    justifyContent: 'space-between',
  },
  Dialog: {
    padding: '10px',
  },
  copyright: {
    marginTop: theme.spacing(5),
  },
});

class LabelEditDialog extends React.Component {

  handleClose = () => {
    this.props.onLabelEditDialogClose();
  };

  onLabelConfirmation = () => {
    let label = document.getElementById('label-edit').value;
    this.props.onLabelConfirmation(this.props.originalLabel, label);
  };

  render() {
	const { classes } = this.props;

	return (
 	<div>
		<Dialog id="label-edit-dialog"
	          open
	          onClose={this.handleClose}
	          scroll={'paper'}
	          aria-labelledby="form-dialog-title"
	        >
	     <div className={classes.title}>
		     <DialogTitle id="form-dialog-title">Label Edit</DialogTitle>
		     <IconButton
		      	id="close-button"
		          aria-label="Close"
		     	onClick={this.handleClose}
			>
		    <CloseIcon />
		    </IconButton>
	     </div>
		     <DialogContent>
			     <DialogContentText>
		              Please enter new content for the label.
		          </DialogContentText>
		          <textarea id="label-edit"
		          	name="label-edit"
		          	rows="20"
		          	cols="80"
		          	defaultValue={this.props.originalLabel}
		          >
				</textarea>
				<Toolbar>
				   <div style={{flexGrow: 0.4}}></div>
		   	   <Button
		         	   color="inherit"
		         	   style={{flexGrow: 0.2}}
		         	   onClick={this.onLabelConfirmation}
		              >
		          	Confirm
		          	</Button>
			  	</Toolbar>
		     </DialogContent>
	     </Dialog>
     </div>
    );
  }
}

LabelEditDialog.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withRoot(withStyles(styles)(LabelEditDialog));